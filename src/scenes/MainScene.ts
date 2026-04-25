import * as Phaser from 'phaser';
import { GAME_HEIGHT, GAME_TITLE, GAME_WIDTH } from '../game/constants';

export class MainScene extends Phaser.Scene {
  constructor() {
    super('MainScene');
  }

  create(): void {
    this.cameras.main.setBackgroundColor('#120f1d');
    this.cameras.main.roundPixels = true;

    const title = this.registry.get('gameTitle') ?? GAME_TITLE;

    this.add.rectangle(GAME_WIDTH / 2, GAME_HEIGHT / 2, GAME_WIDTH, GAME_HEIGHT, 0x120f1d);
    this.add.rectangle(GAME_WIDTH / 2, GAME_HEIGHT / 2 + 48, 220, 72, 0x1d1730, 0.95)
      .setStrokeStyle(2, 0xf0d18c, 0.9);

    this.add.text(GAME_WIDTH / 2, 72, title, {
      fontFamily: 'Arial',
      fontSize: '24px',
      color: '#f7edd2'
    }).setOrigin(0.5);

    this.add.text(GAME_WIDTH / 2, 122, '一叶孤舟入寒江，霜尘落刃起风波', {
      fontFamily: 'Arial',
      fontSize: '10px',
      color: '#c8b98f'
    }).setOrigin(0.5);

    this.add.text(GAME_WIDTH / 2, GAME_HEIGHT / 2 + 34, 'Phaser 4 / TypeScript / Vite', {
      fontFamily: 'Arial',
      fontSize: '12px',
      color: '#9fb7d9'
    }).setOrigin(0.5);

    this.add.text(GAME_WIDTH / 2, GAME_HEIGHT - 28, '主场景已启动，接下来可以接角色、地图与战斗原型。', {
      fontFamily: 'Arial',
      fontSize: '10px',
      color: '#8f97a8'
    }).setOrigin(0.5);
  }
}
